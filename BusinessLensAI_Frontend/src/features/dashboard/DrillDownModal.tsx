import React from 'react';
import { Database, Filter, Download } from 'lucide-react';
import { Modal, DataTable, Button, Badge, toast } from '../../shared/components';

export interface DrillDownModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
}

export const DrillDownModal: React.FC<DrillDownModalProps> = ({ isOpen, onClose, title, subtitle }) => {
  const mockTransactions = [
    { id: 'ORD-9482', customer: 'Acme Corp', category: 'Electronics', amount: '$4,250.00', profit: '$1,105.00', date: '2026-07-05', status: 'Completed' },
    { id: 'ORD-9483', customer: 'Global Tech', category: 'Electronics', amount: '$12,400.00', profit: '$3,224.00', date: '2026-07-05', status: 'Completed' },
    { id: 'ORD-9484', customer: 'Starlight Retail', category: 'Apparel', amount: '$1,850.00', profit: '$462.50', date: '2026-07-04', status: 'Completed' },
    { id: 'ORD-9485', customer: 'Nexus Solutions', category: 'Home Goods', amount: '$3,100.00', profit: '$775.00', date: '2026-07-04', status: 'Processing' },
    { id: 'ORD-9486', customer: 'Vanguard Group', category: 'Electronics', amount: '$8,900.00', profit: '$2,314.00', date: '2026-07-03', status: 'Completed' },
    { id: 'ORD-9487', customer: 'Zenith Logistics', category: 'Accessories', amount: '$950.00', profit: '$285.00', date: '2026-07-03', status: 'Completed' },
    { id: 'ORD-9488', customer: 'Apex Dynamics', category: 'Electronics', amount: '$5,600.00', profit: '$1,456.00', date: '2026-07-02', status: 'Completed' },
    { id: 'ORD-9489', customer: 'Pinnacle Enterprises', category: 'Apparel', amount: '$2,200.00', profit: '$550.00', date: '2026-07-02', status: 'Completed' },
    { id: 'ORD-9490', customer: 'Horizon Media', category: 'Home Goods', amount: '$4,150.00', profit: '$1,037.50', date: '2026-07-01', status: 'Completed' },
    { id: 'ORD-9491', customer: 'Omega Systems', category: 'Electronics', amount: '$15,800.00', profit: '$4,108.00', date: '2026-07-01', status: 'Completed' },
  ];

  const columns = [
    { key: 'id', header: 'Order ID', sortable: true },
    { key: 'customer', header: 'Customer Name', sortable: true },
    { key: 'category', header: 'Category', sortable: true },
    { key: 'amount', header: 'Gross Amount', sortable: true },
    { key: 'profit', header: 'Net Profit', sortable: true },
    { key: 'date', header: 'Date', sortable: true },
    {
      key: 'status',
      header: 'Status',
      render: (row: typeof mockTransactions[0]) => (
        <Badge variant={row.status === 'Completed' ? 'success' : 'warning'} size="sm">
          {row.status}
        </Badge>
      ),
    },
  ];

  const handleExport = () => {
    toast.success('Drill-Down CSV Exported', 'Raw transaction records downloaded successfully.');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Drill-Down Analysis: ${title}`}
      description={subtitle || 'Inspecting underlying physical PostgreSQL transaction records.'}
      size="xl"
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border text-xs">
          <div className="flex items-center gap-2 text-foreground">
            <Database className="w-4 h-4 text-primary" />
            <span>Connected Source: <strong className="font-mono">retail_analytics_db.orders</strong></span>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport} leftIcon={<Download className="w-3.5 h-3.5" />} className="h-7 text-xs">
            Export Records CSV
          </Button>
        </div>

        <DataTable
          data={mockTransactions}
          columns={columns}
          searchKey="customer"
          searchPlaceholder="Search customer or order ID..."
          pageSize={5}
        />

        <div className="flex justify-end pt-2 border-t border-border">
          <Button variant="primary" onClick={onClose}>
            Close Drill-Down View
          </Button>
        </div>
      </div>
    </Modal>
  );
};
